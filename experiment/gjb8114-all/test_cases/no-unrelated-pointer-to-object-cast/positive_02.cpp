class Widget {
public:
    Widget() : value(0) {}
    int value;
};

int main() {
    Widget* widget = new Widget;
    Widget* same = reinterpret_cast<Widget*>(widget);
    same->value = 5;
    delete widget;
    return 0;
}
