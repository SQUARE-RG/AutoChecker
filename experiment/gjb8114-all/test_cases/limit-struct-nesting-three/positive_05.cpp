template <typename T>
struct TemplateOuter {
    struct Level1 {
        struct Level2 {
            T value;
        };
    };
};

int main() {
    return 0;
}
