struct Base {
    int value = 0;
};

class Widget : private Base {
public:
    int getValue() const { return value; }
};

int main() {
    Widget widget;
    return widget.getValue();
}
