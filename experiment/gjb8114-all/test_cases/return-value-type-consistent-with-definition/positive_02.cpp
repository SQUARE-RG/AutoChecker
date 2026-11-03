double fun(double par)
{
    return par * 2.5;
}

int main()
{
    double result = fun(1.0);
    return static_cast<int>(result);
}
