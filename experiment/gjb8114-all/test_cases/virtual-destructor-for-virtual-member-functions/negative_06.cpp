#include <iostream>

class Widget {
public:
    Widget() {}
    virtual void render() { std::cout << 'r'; }
protected:
    ~Widget(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
};

Widget::~Widget() { std::cout << 'd'; }

int main() {
    Widget* w = new Widget();
    w->render();
    return 0;
}
