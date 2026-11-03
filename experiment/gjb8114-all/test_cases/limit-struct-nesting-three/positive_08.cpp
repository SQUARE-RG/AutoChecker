struct Host {
    struct Level2 {
        void build() {
            struct Level3 {};
        }
    };
};

int main() {
    Host::Level2 value;
    value.build();
    return 0;
}
