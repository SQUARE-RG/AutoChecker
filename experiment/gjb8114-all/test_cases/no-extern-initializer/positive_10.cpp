int identity(int v)
{
    return v;
}

extern int (*handler)(int);
int (*handler)(int) = identity;

int main()
{
    return handler(1);
}
