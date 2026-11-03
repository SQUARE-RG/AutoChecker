int select_value(int selector)
{
    int value = 0;
    switch (selector)
    {
        case 1:
            value = selector;
            if (value > 5)
            {
                break;
            }
            value = value + 10;
            break;
        case 2:
            value = selector + 20;
            break;
        default:
            value = selector + 30;
            break;
    }
    return value;
}

int main(int argc, char** argv)
{
    return select_value(argc);
}
