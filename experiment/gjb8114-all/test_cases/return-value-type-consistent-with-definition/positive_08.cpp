char get_char(char value)
{
    return value;
}

int main()
{
    char v = 'A';
    char c = get_char(v);
    return static_cast<int>(c);
}
