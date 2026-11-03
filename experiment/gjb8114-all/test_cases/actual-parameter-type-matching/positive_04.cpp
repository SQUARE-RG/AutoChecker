double scale(double factor);

int main()
{
    double (*fn)(double) = scale;
    double ratio = 1.5;
    return static_cast<int>(fn(ratio));
}

double scale(double factor)
{
    return factor * 2.0;
}
