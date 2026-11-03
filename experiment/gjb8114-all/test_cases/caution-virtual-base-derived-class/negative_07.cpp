struct Base {
    int value = 0;
};

class Widget : virtual private Base {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
public:
    int getValue() const { return value; }
};

int main() {
    Widget widget;
    return widget.getValue();
}
