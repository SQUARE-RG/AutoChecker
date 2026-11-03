int read_value(const int* param)
{
    if (param == nullptr)
    {
        return 0;
    }
    return *param;
}

int process(const int* param)
{
    return read_value(param);
}

int main()
{
    int value = 7;
    return process(&value);
}
