#include <iostream>

class Widget {
public:
    inline int GetValue() const;
    void SetValue(int v);
private:
    int value_ = 0;
};

inline int Widget::GetValue() const {
    return value_;
}

void Widget::SetValue(int v) {
    value_ = v;
}

int main() {
    Widget w;
    w.SetValue(21);
    std::cout << w.GetValue() << '\n';
    return 0;
}
