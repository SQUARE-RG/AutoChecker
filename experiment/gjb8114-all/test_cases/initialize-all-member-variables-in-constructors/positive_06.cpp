class ConditionalInit {
public:
    ConditionalInit(bool chooseFirst) {
        if (chooseFirst) {
            primary = 10;
        } else {
            primary = 20;
        }
        secondary = 5;
    }
    int total() const { return primary + secondary; }
private:
    int primary;
    int secondary;
};

int main() {
    ConditionalInit c(true);
    return c.total();
}
