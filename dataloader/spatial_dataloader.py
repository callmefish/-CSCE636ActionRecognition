import pickle
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import random
from .split_train_test_video import *
from skimage import io, color, exposure
import torch

class spatial_dataset(Dataset):  
    def __init__(self, dic, root_dir, mode, transform=None):
 
        self.keys = list(dic.keys())
        self.values = list(dic.values())
        self.root_dir = root_dir
        self.mode = mode
        self.transform = transform

    def __len__(self):
        return len(self.keys)

    def load_ucf_image(self,video_name, index):
        
        path = self.root_dir + 'v_'+video_name + '/frame'
         
        img = Image.open(path + '_' + str(index).zfill(6) + '.jpg')
        transformed_img = self.transform(img)
        img.close()

        return transformed_img

   
    def __getitem__(self, idx):

        if self.mode == 'train':
            video_name, nb_clips = self.keys[idx-1].split(' ')
            nb_clips = int(nb_clips)
            clips = []
            clips.append(random.randint(1, nb_clips//3))
            for i in range(1, 3):
                clips.append(random.randint(i * nb_clips // 3, (i+1) * nb_clips // 3))
            # 任意选取三帧图片
            #clips.append(random.randint(1, nb_clips//3))
            #clips.append(random.randint(nb_clips//3, nb_clips*2//3))
            #clips.append(random.randint(nb_clips*2//3, nb_clips+1))
            
        elif self.mode == 'val':
            video_name, index = self.keys[idx-1].split(' ')
            index =abs(int(index))
        else:
            raise ValueError('There are only train and val mode')

        label = self.values[idx-1]
        label = int(label)-1
        
        if self.mode == 'train':
            data ={}
            for i in range(len(clips)):
                key = 'img'+str(i)
                index = clips[i]
                data[key] = self.load_ucf_image(video_name, index)
                    
            sample = (data, label)
        elif self.mode == 'val':
            data = self.load_ucf_image(video_name,index)
            
            sample = (video_name, data, label)
        else:
            raise ValueError('There are only train and val mode')
           
        return sample

class spatial_dataloader():
    def __init__(self, BATCH_SIZE, num_workers, path, ucf_list, ucf_split):

        self.BATCH_SIZE=BATCH_SIZE
        self.num_workers=num_workers
        self.data_path=path
        self.frame_count ={}
        # split the training and testing videos
        splitter = UCF101_splitter(path=ucf_list,split=ucf_split)
        self.train_video, self.test_video = splitter.split_video()

   
    def load_frame_count(self):
        # print '==> Loading frame number of each video'
        with open('/home/yzy20161103/demo/CSCE636ActionRecognition/dataloader/dic/frame_count.pickle','rb') as file:
           dic_frame = pickle.load(file)
        file.close()

        for line in dic_frame :
            videoname = line.split('_',1)[1].split('.',1)[0]
#             n,g = videoname.split('_',1)
#             if n == 'HandStandPushups':
#                 videoname = 'HandstandPushups_'+ g
            self.frame_count[videoname]=dic_frame[line]

    def run(self):
        self.load_frame_count()
        self.get_training_dic()
        self.val_sample20()
        train_loader = self.train()
        val_loader = self.validate()

        return train_loader, val_loader, self.test_video

    
    def get_training_dic(self):
        #print '==> Generate frame numbers of each training video'
        self.dic_training={}
        for video in self.train_video:
            #print videoname
            nb_frame = self.frame_count[video]-10+1
            key = video+' '+ str(nb_frame)
            self.dic_training[key] = self.train_video[video]
                    
    def val_sample20(self):
        print('==> sampling testing frames')
        self.dic_testing={}
        for video in self.test_video:
            nb_frame = self.frame_count[video]-10+1
            # 分成19个片段
            interval = int(nb_frame/19)
            for i in range(19):
                frame = i*interval
                key = video+ ' '+str(frame+1)
                self.dic_testing[key] = self.test_video[video]      

    def train(self):
        training_set = spatial_dataset(dic=self.dic_training, root_dir=self.data_path, mode='train', transform = transforms.Compose([
                transforms.RandomCrop(224),
                transforms.RandomHorizontalFlip(),
                #transforms.ColorJitter(brightness=0, contrast=0, saturation=0, hue=0),
                #transforms.RandomRotation(30), 
                transforms.ToTensor(),
          
                transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])
                ]))
        print('==> Training data :',len(training_set)*10,'frames')
        # sample = (video_name, data, label), extract data['img1']
        print(training_set[1][0]['img1'].size())

        train_loader = DataLoader(
            dataset=training_set, 
            batch_size=self.BATCH_SIZE,
            shuffle=True,
            num_workers=self.num_workers)
        return train_loader

    def validate(self):
        validation_set = spatial_dataset(dic=self.dic_testing, root_dir=self.data_path, mode='val', transform = transforms.Compose([
                transforms.Resize([224,224]),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])
                ]))
        
        print('==> Validation data :',len(validation_set),'frames')
        # sample = (video_name, data, label), extract data
        print(validation_set[0][1].size())

        val_loader = DataLoader(
            dataset=validation_set, 
            batch_size=self.BATCH_SIZE, 
            shuffle=False,
            num_workers=self.num_workers)
        return val_loader





if __name__ == '__main__':
    
    dataloader = spatial_dataloader(BATCH_SIZE=1, num_workers=1, 
                                path='/home/yzy20161103/csce636_project/project/video_data_497_sim/', 
                                ucf_list='/home/yzy20161103/csce636_project/project/UCF_list/',
                                ucf_split='01')
    train_loader,val_loader,test_video = dataloader.run()
