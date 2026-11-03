unsigned int transform(unsigned int value)
{
    unsigned int result = value;

#define MASK_LOW 0xFFU
    result = result & MASK_LOW;
#undef MASK_LOW

#define SHIFT_BITS 2U
    result = result << SHIFT_BITS;
#undef SHIFT_BITS

    return result;
}

int main()
{
    return static_cast<int>(transform(1024U));
}
