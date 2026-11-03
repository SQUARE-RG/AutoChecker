int fallthrough_value(int code)
{
    int result = 0;
    switch (code)
    {
    case 1:
        [[fallthrough]];
    default:
        result = 2;
        break;
    }
    return result;
}

int main()
{
    return fallthrough_value(1);
}
