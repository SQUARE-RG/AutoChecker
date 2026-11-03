static int compute_value(int data)
{
    return 2 * data;
}

int main()
{
    int input = 3;
    int result = compute_value(input);
    return result == 6 ? 0 : 1;
}
