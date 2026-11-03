int compute(int input)
{
    int result = input;
    if (input < 0)
    {
        goto finish;
    }
    result = result + 1;
finish:
    return result;
}

int main(int argc, char** argv)
{
    return compute(argc);
}
