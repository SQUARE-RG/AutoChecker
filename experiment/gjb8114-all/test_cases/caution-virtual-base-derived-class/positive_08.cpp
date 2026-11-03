struct Interface {
    virtual ~Interface() = default;
    virtual int value() const = 0;
};

class Widget final : public Interface {
public:
    int value() const override { return 7; }
};

int main() {
    Widget widget;
    return widget.value();
}
