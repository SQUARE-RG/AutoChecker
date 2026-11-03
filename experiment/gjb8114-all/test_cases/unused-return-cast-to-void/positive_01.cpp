int compute_sign(int value)
{
    return value >= 0 ? 1 : -1;
}

int main()
{
    int local = -5;
    int sign = compute_sign(local);
    return sign > 0 ? 0 : 1;
}
