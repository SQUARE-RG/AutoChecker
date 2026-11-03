int main() {
    int score = 100;
    {
        int bonus = 50;
        bonus += 10;
    }
    return score;
}
