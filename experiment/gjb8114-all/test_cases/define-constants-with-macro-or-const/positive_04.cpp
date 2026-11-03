const int kNotFound = 404;

bool is_not_found(int code) {
  switch (code) {
    case kNotFound:
      return true;
    default:
      return false;
  }
}

int main(int argc, char** argv) {
  return is_not_found(argc);
}
