int main()
{
    int result = 0;
    auto classify = [&result](int value) -> void
    {
        if (value == 0)
        {
            result = 1;
        }
        else if (value == 1)
        {
            result = 2;
        }
        else
        {
            result = 3;
        }
    };
    classify(2);
    return result;
}
