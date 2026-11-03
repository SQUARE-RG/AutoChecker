#include <iostream>

class Widget {
public:
    inline int GetValue() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
        return value_;
    }

    void SetValue(int v);
private:
    int value_ = 0;
};

void Widget::SetValue(int v) {
    value_ = v;
}

int main() {
    Widget w;
    w.SetValue(21);
    std::cout << w.GetValue() << '\n';
    return 0;
}
