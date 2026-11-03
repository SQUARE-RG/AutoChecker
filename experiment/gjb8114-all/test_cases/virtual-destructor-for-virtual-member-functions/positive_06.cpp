#include <iostream>

class Widget {
public:
    Widget() {}
    virtual void render() { std::cout << 'r'; }
protected:
    virtual ~Widget();
};

Widget::~Widget() { std::cout << 'd'; }

int main() {
    Widget* w = new Widget();
    w->render();
    return 0;
}
