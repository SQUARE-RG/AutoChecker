int main()
{
    double a = 1.0;
    double b = 1.000001;
    double eps = 1e-5;
    if (a < b + eps && a > b - eps) {
        return 1;
    }
    return 0;
}
