unsigned int compute_value()
{
    unsigned int value = 0U;
#define LOCAL_FACTOR 3U
    value = value + LOCAL_FACTOR;
#undef LOCAL_FACTOR
    return value;
}

int main()
{
    return static_cast<int>(compute_value());
}
