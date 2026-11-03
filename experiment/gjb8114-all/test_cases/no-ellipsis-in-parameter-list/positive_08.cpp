struct Widget
{
};

int main()
{
    int (Widget::*pmf)(int, int) = nullptr;
    (void)pmf;
    return 0;
}
