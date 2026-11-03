void touch()
{
}

struct Widget
{
    int value;

    Widget() : value(((void)touch(), 0)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    {
    }
};

int main()
{
    Widget widget;
    return widget.value;
}
