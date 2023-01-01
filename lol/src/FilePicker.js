import React, {useState} from 'react'
import { FileDrop } from 'react-file-drop'
import {useRef } from 'react'
import { Typography } from '@mui/material';
import "./f.css"
import axios from 'axios'
import CenteredTabs from "./Table"
import NoteAddOutlinedIcon from '@mui/icons-material/NoteAddOutlined';
import CircularProgress from '@mui/material/CircularProgress';

export default function FilePicker() {
    const [isFilePicked, setIsFiledPicked] = useState(false)
    const [data, setData] = useState()
    
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
    }

    const styles = {border: '1px solid black', width: 600, color: 'black', padding: 20 };
    return (
    <React.Fragment>
        {data? 
        <div style={{marginLeft:"100px", marginTop:"20px"}}><CenteredTabs onApprove={approve} onDiscard={discard} data={data}/></div>:
        <div style={{border:"1px dotted grey", marginTop:"20px", marginLeft:"100px"}}>
          <FileDrop
            onDrop={(files, event) => changeHandler(files, event)}
            onTargetClick={changeHandler}>
              {isFilePicked? <CircularProgress />:<NoteAddOutlinedIcon />}
              <Typography>Drag and Drop XML file</Typography> 
          </FileDrop>
        </div>
        }
    </React.Fragment>
    );
}

