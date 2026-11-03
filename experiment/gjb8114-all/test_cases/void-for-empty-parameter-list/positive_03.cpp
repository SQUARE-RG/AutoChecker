struct Widget {
    int getValue(void) { return 7; }
};

int main(void)
{
    Widget widget;
    int value = widget.getValue();
    return value == 7 ? 0 : 1;
}
