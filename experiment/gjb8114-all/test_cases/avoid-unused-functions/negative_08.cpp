namespace {

class Widget {
public:
    Widget() = default;

    int width() const {
        return width_;
    }

protected:
    void helper() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
        width_ += 1;
    }

private:
    int width_ = 0;
};

} // namespace

int main() {
    Widget w;
    (void)w.width();
    return 0;
}
