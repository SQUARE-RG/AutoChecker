struct Widget {
    int getValue() { return 7; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]
};

int main(void)
{
    Widget widget;
    int value = widget.getValue();
    return value == 7 ? 0 : 1;
}
