import React, {useState, useEffect} from 'react'
import { FileDrop } from 'react-file-drop'
import { Typography } from '@mui/material';
import "./f.css"
import axios from 'axios'
import CenteredTabs from "./Table"
import NoteAddOutlinedIcon from '@mui/icons-material/NoteAddOutlined';
import CircularProgress from '@mui/material/CircularProgress';

export default function FilePicker() {
    const [isFilePicked, setIsFiledPicked] = useState(false)
    const [data, setData] = useState()

    // useEffect(() => {
    //   const storedData = window.localStorage.getItem('data')
    //   console.log(storedData)
    //   console.log(storedData === null)
    //   if(typeof storedData !== undefined){
    //     console.log('omg')
    //     setData(JSON.parse(storedData))
    //   }
    // }, []);
    // useEffect(() => {
    //   window.localStorage.setItem('data', JSON.stringify(data));
    // }, [data]);

    const changeHandler = (files, event) => {
      if(typeof files[0] === "undefined" || files[0].type != "text/xml"){
        console.log('File not supported')
        return
      }
      setIsFiledPicked(true)
      if (files[0]) {
        const url = "http://127.0.0.1:8000/"
        // const headers = {
        //   "Access-Control-Allow-Origin":"*", 
        //   "Access-Control-Allow-Headers":"Origin, X-Requested-With, Content-Type, Accept"
        // }
        // const config = {
        //   headers:headers
        // }
        const data = new FormData() 
        data.append('upload_file', files[0])

        axios.post(url, data).then(res => 
        {
            console.log(res)
            console.log(res.data.branches)
            setData(res.data)
        }); 
        console.log(files[0])
      }

    }
//    const onTargetClick = () => {
        //fileInputRef.current.click()
        //console.log(selectedFile)
      //}
    const discard = () => {
      if(window.confirm("Are you sure you want to discard this batch?")){
        setIsFiledPicked(false)
        setData()
      }
    }

    const approve = () => {
      //console.log("approving batch " + data['batch_id'])
      const data = new FormData() 
      data.append('type', 'payments')
      data.append('batch_id', 'xd')
      axios({
        url: 'http://127.0.0.1:8000/getCsv/',
        method: 'POST',
        data:data,
        responseType: 'blob', // important
      }).then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'payment.csv');
        document.body.appendChild(link);
        link.click();
      });
    }

    const styles = {border: '1px solid black', width: 600, color: 'black', padding: 20 };
    return (
    <React.Fragment>
        <Typography mt="20px" variant={'h4'} align="center">New Payment</Typography>
        {data? 
        <div style={{marginTop:"20px"}}><CenteredTabs onApprove={approve} onDiscard={discard} data={data}/></div>:
        <div style={{border:"1px dotted grey", marginTop:"20px"}}>
          <input hidden accept="image/*" multiple type="file" />
          <FileDrop
            onDrop={(files, event) => changeHandler(files, event)}
            >
              {isFilePicked? <CircularProgress />:<NoteAddOutlinedIcon />}
              <Typography>Drag and Drop XML file</Typography> 
          </FileDrop>
        </div>
        }
    </React.Fragment>
    );
}

