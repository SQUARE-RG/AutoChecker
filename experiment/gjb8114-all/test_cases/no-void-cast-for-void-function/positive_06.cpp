void touch()
{
}

struct Widget
{
    int value;

    Widget() : value((touch(), 0))
    {
    }
};

int main()
{
    Widget widget;
    return widget.value;
}
