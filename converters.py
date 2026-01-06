# Converters for Tamagotchi IR protocol
# Converts between bit strings and IR pulse timing lengths

# Tamagotchi IR timing constants (microseconds)
LEADER_MARK = 9500
LEADER_GAP = 6000
DATA_MARK = 600
SHORT_GAP = 600   # Represents "0" bit
LONG_GAP = 1200   # Represents "1" bit
END_MARK = 1200


def to_lengths(bits):
    """
    Convert a bit string to IR pulse timing lengths.
    
    Args:
        bits: String of "0" and "1" characters
        
    Returns:
        List of pulse lengths in microseconds
    """
    output = [LEADER_MARK, LEADER_GAP]
    for b in bits:
        if int(b) == 0:
            output += [DATA_MARK, SHORT_GAP]
        else:
            output += [DATA_MARK, LONG_GAP]
    output += [END_MARK]
    return output


def to_bits(lengths):
    """
    Convert IR pulse timing lengths back to bits.
    
    Args:
        lengths: List of pulse lengths in microseconds
        
    Returns:
        Tuple of (bit_count, bit_list) where bit_list contains 0s and 1s
    """
    # Handle truncated headers (sometimes the receiver misses the start)
    if len(lengths) > 40 and lengths[0] < 1500 and lengths[1] < 1500:
        lengths = [9000, 6000] + lengths
    elif len(lengths) > 40 and 5000 < lengths[0] < 7000 and lengths[1] < 1500:
        lengths = [9000] + lengths

    # Validate header
    if len(lengths) < 2:
        return (0, [])
    if not (8000 < lengths[0] < 10000):
        return (0, [])
    if not (5000 < lengths[1] < 7000):
        return (0, [])

    # Decode data bits (skip header, look at gaps only)
    output = []
    for i, length in enumerate(lengths[2:]):
        # Only look at gaps (even indices after header)
        if i % 2 == 0:
            continue
        if length < 900:
            output.append(0)
        elif length < 2000:
            output.append(1)

    return (len(output), output)
