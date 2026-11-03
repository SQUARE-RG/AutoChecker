bool accept(bool value)
{
    return value;
}

int main()
{
    int signed_value = -2;
    unsigned int unsigned_value = 2U;
    accept(signed_value < static_cast<int>(unsigned_value));
    return 0;
}
