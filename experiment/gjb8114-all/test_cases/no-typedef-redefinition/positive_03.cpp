int first()
{
    typedef int mytype;
    mytype value = 3;
    return value;
}

double second()
{
    typedef double mytype;
    mytype value = 1.5;
    return value;
}

int main()
{
    int a = first();
    double b = second();
    return (a == 3 && b > 1.0) ? 0 : 1;
}
