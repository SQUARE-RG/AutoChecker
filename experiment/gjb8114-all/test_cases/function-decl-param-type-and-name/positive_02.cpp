int compute(const char* text, int length, double scale = 1.0);

int main()
{
    return compute("abc", 3);
}

int compute(const char* text, int length, double scale)
{
    return length + static_cast<int>(scale);
}
