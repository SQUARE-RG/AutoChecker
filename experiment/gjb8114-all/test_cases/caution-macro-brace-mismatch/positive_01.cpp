#define IF0(x) if (0 == (x))

int main(void)
{
    int test = 0;
    IF0(test)
    {
        test = test + 1;
    }
    return 0;
}
