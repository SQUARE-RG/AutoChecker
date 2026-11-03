namespace {

class Widget {
public:
    Widget() = default;

    int width() const {
        return width_;
    }

protected:
    void helper() {
        width_ += 1;
    }

private:
    int width_ = 0;
};

class SubWidget : public Widget {
public:
    int run() {
        helper();
        return width();
    }
};

} // namespace

int main() {
    SubWidget w;
    return w.run();
}
