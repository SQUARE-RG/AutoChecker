int apply_clamp(int value);

int main()
{
    return apply_clamp(-9) == 0 ? 0 : 1;
}

static int clamp_low(int value)
{
    return value < 0 ? 0 : value;
}

int apply_clamp(int value)
{
    return clamp_low(value);
}
