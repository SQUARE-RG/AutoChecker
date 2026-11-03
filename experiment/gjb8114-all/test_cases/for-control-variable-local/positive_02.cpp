// The for loop control variable is a local variable declared inside the function.

int compute()
{
    int value = 1;
    int result = 0;
    for (value = 1; value <= 5; value++)
    {
        result += value;
    }
    return result;
}

int main()
{
    return compute();
}
