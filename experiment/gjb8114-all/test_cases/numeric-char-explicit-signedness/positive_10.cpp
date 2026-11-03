struct Flags {
    signed char level : 4;
    int score;
};

int main() {
    Flags f;
    f.level = 2;
    f.score = f.level + 1;
    return f.score;
}
