short get_short(short value)
{
    return value;
}

int main()
{
    short v = 7;
    short s = get_short(v);
    return static_cast<int>(s);
}
