int main()
{
    static_assert((sizeof(int) >= 1) && (sizeof(long) >= 1), "type sizes must be positive");
    return 0;
}
