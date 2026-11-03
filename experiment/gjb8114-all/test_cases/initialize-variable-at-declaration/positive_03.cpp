class Temperature {
public:
    Temperature() = default;

    void set(int c) { celsius_ = c; }
    int get() const { return celsius_; }

private:
    int celsius_ = 0;
};

int main() {
    Temperature t;
    t.set(25);
    return t.get() == 25 ? 0 : 1;
}
