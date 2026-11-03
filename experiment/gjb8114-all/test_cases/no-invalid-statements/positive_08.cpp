int positive_08(int value)
{
    int result = (value += 1);
    return result;
}

int main()
{
    return positive_08(0);
}
