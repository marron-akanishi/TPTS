import dlib

if __name__ == "__main__":

    TrainingXml = "all.xml"
    SvmFile = "detector_face.svm"
    # 訓練用オプションの作成
    options = dlib.simple_object_detector_training_options()
    # 左右反転画像を生成するか
    options.add_left_right_image_flips = True
    # 一枚の画像からどれだけサンプルを作るか
    options.upsample_limit = 5
    # SVM用のC値
    options.C = 100
    # どれだけスレッド使うか
    options.num_threads = 4
    # 学習許容範囲
    options.epsilon = 0.001
    # 学習状況を出力するか
    options.be_verbose = True

    dlib.train_simple_object_detector(TrainingXml, SvmFile, options)