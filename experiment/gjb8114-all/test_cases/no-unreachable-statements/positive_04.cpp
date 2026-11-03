int positive_04(int n)
{
    int sum = 0;
    for (int i = 0; i < n; ++i) {
        if (i == 2) {
            continue;
        }
        sum += i;
    }
    return sum;
}

int main()
{
    return positive_04(5);
}
