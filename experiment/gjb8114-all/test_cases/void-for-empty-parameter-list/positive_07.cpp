extern int fetchValue(void);

static int datax = 0;

int main(void)
{
    datax = 1;
    return fetchValue();
}

int fetchValue(void)
{
    return datax;
}
