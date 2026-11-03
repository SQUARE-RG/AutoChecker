bool is_ge(long long signed_value, unsigned long long unsigned_value)
{
    return signed_value >= static_cast<long long>(unsigned_value);
}

int main()
{
    return is_ge(-1LL, 1ULL) ? 0 : 1;
}
