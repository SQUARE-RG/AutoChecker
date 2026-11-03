struct FlagPair {
    bool result;
    FlagPair(bool left, bool right) : result(left && !right) {
    }
};

int main() {
    FlagPair pair(true, false);
    return pair.result ? 0 : 1;
}
